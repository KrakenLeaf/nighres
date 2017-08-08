import os
import urllib
import numpy as np
import nibabel as nb
import nighres
from utils import _download_from_url


out_dir = '/SCR/data/nighres_testing/'
t1map = os.path.join(out_dir, "T1map.nii.gz")
t1w = os.path.join(out_dir, "T1w.nii.gz")
# TODO: where to get the INV2 file?

_download_from_url("http://openscience.cbs.mpg.de/bazin/7T_Quantitative/MP2RAGE-05mm/subject01_mp2rage_0p5iso_qT1.nii.gz", t1map)  # noqa

_download_from_url("http://openscience.cbs.mpg.de/bazin/7T_Quantitative/MP2RAGE-05mm/subject01_mp2rage_0p5iso_uni.nii.gz", t1w)  # noqa

data_dir = '/SCR/data/cbstools_testing/'
inv2 = data_dir + '7t_trt/test_nii/INV2.nii.gz'
# out_dir = '/SCR/data/cbstools_testing/out/'
# t1w = data_dir + '7t_trt/test_nii/T1w.nii.gz'
# t1map = data_dir + '7t_trt/test_nii/T1map.nii.gz'

# Skullstripping of MP2RAGE images
skullstripping_results = nighres.mp2rage_skullstripping(
                                                        second_inversion=inv2,
                                                        t1_weighted=t1w,
                                                        t1_map=t1map,
                                                        save_data=True,
                                                        output_dir=out_dir)

# MGDM segmentation using both the T1 weighted and image
segmentation_results = nighres.mgdm_segmentation(
                        contrast_image1=skullstripping_results.t1w_masked,
                        contrast_type1="Mp2rage7T",
                        contrast_image2=skullstripping_results.t1map_masked,
                        contrast_type2="T1map7T",
                        save_data=True, output_dir=out_dir)


# Creating binary representations of the GM/WM and GM/CSF boundaries from the
# segmentation output
wm = [11, 12, 13, 17, 18, 30, 31, 32, 33, 34, 35, 36, 37,
      38, 39, 40, 41, 47, 48]
gm = [26, 27]

segmentation = segmentation_results['segmentation'].get_data()
wm_mask = np.zeros(segmentation.shape)
for x in wm:
    wm_mask[np.where(segmentation == x)] = 1
wm_nii = nb.Nifti1Image(wm_mask,
                        segmentation_results['segmentation'].get_affine())

gm_mask = np.copy(wm_mask)
for x in gm:
    gm_mask[np.where(segmentation == x)] = 1
gm_nii = nb.Nifti1Image(gm_mask,
                        segmentation_results['segmentation'].get_affine())

# Creating levelsets from binary tissue images
gm_wm_levelset = nighres.create_levelsets(wm_mask, save_data=True)
gm_csf_levelset = nighres.create_levelsets(gm_mask, save_data=True)

# Perform volumetric layering of the cortical sheet
depth, layers, boundaries = nighres.layering(gm_wm_levelset,
                                                    gm_csf_levelset,
                                                    n_layers=3,
                                                    save_data=False)

# sample t1 across cortical layers
profiles = nighres.profile_sampling(boundaries, t1map,
                                           save_data=False)

# t1map_stripped = data_dir + 'cbsopen/t1map_1mm.nii.gz'
# t1w_stripped = data_dir + 'cbsopen/uni_1mm.nii.gz'
# segmentation_results = nighres.mgdm_segmentation(
#                         contrast_image1=t1w_stripped,
#                         contrast_type1="Mp2rage7T",
#                         contrast_image2=t1map_stripped,
#                         contrast_type2="T1map7T",
#                         save_data=True, output_dir=out_dir)







# from nilearn import plotting
# import matplotlib.pyplot as plt
# from nilearn._utils.niimg_conversions import _index_img
#n_layers = 3
#coords = (-5, -2, 1)
#gwb_prob = './data/adult_F04_intern_orig_binmask.nii.gz'
#cgb_prob = './data/adult_F04_extern_orig_binmask.nii.gz'
#intensity = './data/F04_01032013_MSME_TEsum_magn_initial.nii'
#mesh = './data/adult_F04_midcortical_surf.vtk'
# fig1 = plt.figure(figsize=(20, 8))
# ax1 = fig1.add_subplot(211)
# plotting.plot_anat(gwb_prob, annotate=False, draw_cross=False,
#                    display_mode='z', cut_coords=coords,
#                    figure=fig1, axes=ax1, title='GM/WM boundary', vmax=1)
# ax2 = fig1.add_subplot(212)
# plotting.plot_anat(cgb_prob, annotate=False, draw_cross=False,
#                    display_mode='z', cut_coords=coords,
#                    figure=fig1, axes=ax2, title='GM/CSF boundary', vmax=1)
#
# fig2 = plt.figure(figsize=(20, 8))
# ax1 = fig2.add_subplot(211)
# plotting.plot_anat(gwb, annotate=False, draw_cross=False,
#                    display_mode='z', cut_coords=coords,
#                    figure=fig2, axes=ax1, title='GM/WM boundary',
#                    vmin=gwb.get_data().min())
# ax2 = fig2.add_subplot(212)
# plotting.plot_anat(cgb, annotate=False, draw_cross=False,
#                    display_mode='z', cut_coords=coords,
#                    figure=fig2, axes=ax2, title='GM/CSF boundary',
#                    vmin=cgb.get_data().min())
#
#
# fig3 = plt.figure(figsize=(20, 8))
# ax1 = fig3.add_subplot(211)
# plotting.plot_img(depth, annotate=False, draw_cross=False,
#                   display_mode='z', cut_coords=coords,
#                   figure=fig3, axes=ax1, title='Equivolumetric depth',
#                   cmap='inferno')
# ax2 = fig3.add_subplot(212)
# plotting.plot_img(layers, annotate=False, draw_cross=False, display_mode='z',
#                   cut_coords=coords, figure=fig3, axes=ax2,
#                   title='Equivolumetric layers', cmap='gnuplot',
#                   vmin=0, vmax=5)
#
#
# fig4 = plt.figure(figsize=(20, (n_layers + 1) * 4))
# for i in range(n_layers + 1):
#     ax = fig4.add_subplot(n_layers + 1, 1, i + 1)
#     plotting.plot_img(_index_img(profiles, i), annotate=False,
#                       draw_cross=False, display_mode='z',
#                       cut_coords=coords, figure=fig4, axes=ax,
#                       title='Depth %s' % str(i), cmap='inferno',
#                       vmin=0, vmax=0.6 * 1e8)
# plotting.show()